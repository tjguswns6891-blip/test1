using PKHeX.Core;

namespace PKHeXMobile.Services;

/// <summary>
/// Which storage area a slot lives in.
/// </summary>
public enum SlotArea { Party, Box }

/// <summary>
/// A single slot reference within the loaded save file.
/// </summary>
public readonly record struct SlotRef(SlotArea Area, int Box, int Slot)
{
    public StorageSlotType SlotType => Area == SlotArea.Party ? StorageSlotType.Party : StorageSlotType.Box;
}

/// <summary>
/// Holds the currently loaded save file and wraps the PKHeX.Core calls the UI needs.
/// </summary>
public sealed class AppState
{
    public const string Language = "ko";

    public SaveFile? Sav { get; private set; }
    public string FileName { get; private set; } = "";
    public FilteredGameDataSource Sources { get; private set; }
    public bool HasUnsavedChanges { get; private set; }

    public AppState()
    {
        GameInfo.CurrentLanguage = Language;
        GameInfo.Strings = GameInfo.GetStrings(Language);
        Sources = new FilteredGameDataSource(FakeSaveFile.Default, GameInfo.Sources);
    }

    public GameStrings Strings => GameInfo.Strings;

    /// <summary>
    /// Tries to read <paramref name="data"/> as a save file.
    /// </summary>
    /// <returns>An error message on failure; otherwise null.</returns>
    public string? Load(byte[] data, string fileName)
    {
        if (!SaveUtil.TryGetSaveFile(data, out var sav, fileName))
            return "세이브 파일 형식을 인식하지 못했어요. 에뮬레이터에서 내보낸 원본 세이브 파일인지 확인해 주세요.";

        Sav = sav;
        FileName = fileName;
        Sources = new FilteredGameDataSource(sav, GameInfo.Sources);
        HasUnsavedChanges = false;
        return null;
    }

    public void Close()
    {
        Sav = null;
        FileName = "";
        HasUnsavedChanges = false;
    }

    public byte[] Export()
    {
        var sav = Sav ?? throw new InvalidOperationException("No save loaded.");
        var data = sav.Write().ToArray();
        HasUnsavedChanges = false;
        return data;
    }

    public string GameName => Sav is null ? "" : GameInfo.GetVersionName(Sav.Version);

    public string GetBoxName(int box) => Sav switch
    {
        IBoxDetailNameRead named when GetSafeBoxName(named, box) is { Length: > 0 } name => name,
        _ => $"박스 {box + 1}",
    };

    private static string GetSafeBoxName(IBoxDetailNameRead named, int box)
    {
        try { return named.GetBoxName(box).Trim(); }
        catch { return ""; }
    }

    /// <summary>
    /// Gets the entity in a slot. Empty party slots past the end of the party return a blank entity.
    /// </summary>
    public PKM Get(SlotRef slot)
    {
        var sav = Sav!;
        if (slot.Area == SlotArea.Party)
            return slot.Slot < sav.PartyCount ? sav.GetPartySlotAtIndex(slot.Slot) : sav.BlankPKM;
        return sav.GetBoxSlotAtIndex(slot.Box, slot.Slot);
    }

    public bool IsLocked(SlotRef slot)
        => slot.Area == SlotArea.Box && Sav!.IsBoxSlotOverwriteProtected(slot.Box, slot.Slot);

    /// <summary>
    /// Creates a starting entity for an empty slot, filled with the save's trainer details.
    /// </summary>
    public PKM CreateNew()
    {
        var sav = Sav!;
        var pk = sav.BlankPKM;
        EntityTemplates.TemplateFields(pk, sav);
        // Gen 6+ games give every Pokémon an encryption constant separate from its PID.
        if (pk.Format >= 6)
            pk.SetRandomEC();
        pk.CurrentLevel = 5;
        pk.ResetPartyStats();
        return pk;
    }

    public void Set(SlotRef slot, PKM pk)
    {
        var sav = Sav!;
        if (slot.Area == SlotArea.Party)
        {
            pk.ResetPartyStats();
            // A new party member always goes to the end of the party.
            var index = Math.Min(slot.Slot, sav.PartyCount);
            sav.SetPartySlotAtIndex(pk, index);
        }
        else
        {
            sav.SetBoxSlotAtIndex(pk, slot.Box, slot.Slot);
        }
        HasUnsavedChanges = true;
    }

    /// <summary>
    /// Clears a slot.
    /// </summary>
    /// <returns>An error message when the slot cannot be cleared; otherwise null.</returns>
    public string? Delete(SlotRef slot)
    {
        var sav = Sav!;
        if (slot.Area == SlotArea.Party)
        {
            if (sav.PartyCount <= 1)
                return "파티에는 최소 한 마리가 있어야 해요.";
            sav.DeletePartySlot(slot.Slot);
        }
        else
        {
            sav.SetBoxSlotAtIndex(sav.BlankPKM, slot.Box, slot.Slot);
        }
        HasUnsavedChanges = true;
        return null;
    }

    public string GetSpeciesName(ushort species)
    {
        var list = Strings.specieslist;
        return species < list.Length ? list[species] : $"#{species}";
    }

    public string GetDisplayName(PKM pk)
    {
        if (pk.IsEgg)
            return "알";
        var species = GetSpeciesName(pk.Species);
        return pk.IsNicknamed && !string.IsNullOrWhiteSpace(pk.Nickname) ? $"{pk.Nickname} ({species})" : species;
    }

    public static string GetSpriteUrl(PKM pk)
        => pk.IsShiny
            ? $"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{pk.Species}.png"
            : $"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pk.Species}.png";

    public static LegalityAnalysis Analyze(PKM pk, SlotRef slot) => new(pk, slot.SlotType);

    public static string Report(LegalityAnalysis la) => la.Report(Language, verbose: false);
}
