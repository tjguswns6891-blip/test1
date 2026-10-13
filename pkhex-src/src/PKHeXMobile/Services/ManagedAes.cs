using System.Security.Cryptography;
using PKHeX.Core;

namespace PKHeXMobile.Services;

/// <summary>
/// Pure C# AES for the browser, where .NET's <see cref="Aes"/> throws <see cref="PlatformNotSupportedException"/>.
/// </summary>
/// <remarks>
/// PKHeX.Core needs AES to sign Gen 7 (Sun/Moon, Ultra Sun/Ultra Moon) saves, and plugs it in through
/// <see cref="RuntimeCryptographyProvider.Aes"/>. Only unpadded ECB and CBC are used, so that is all this supports.
/// Speed is not a concern: the signed regions are a few hundred bytes.
/// </remarks>
public sealed class ManagedAesProvider : IAesCryptographyProvider
{
    public IAesCryptographyProvider.IAes Create(byte[] key, CipherMode mode, PaddingMode padding, byte[]? iv = null)
    {
        if (padding != PaddingMode.None)
            throw new NotSupportedException($"Padding mode {padding} is not supported.");
        return new ManagedAes(key, iv);
    }
}

public sealed class ManagedAes : IAesCryptographyProvider.IAes
{
    private const int BlockSize = 16;

    private readonly uint[] _keys;
    private readonly int _rounds;
    private readonly byte[] _iv;

    public ManagedAes(byte[] key, byte[]? iv = null)
    {
        if (key.Length is not (16 or 24 or 32))
            throw new ArgumentException("AES key must be 16, 24, or 32 bytes.", nameof(key));
        _rounds = (key.Length / 4) + 6;
        _keys = ExpandKey(key, _rounds);
        _iv = iv is null ? new byte[BlockSize] : (byte[])iv.Clone();
    }

    public void Dispose() { }

    public void EncryptEcb(ReadOnlySpan<byte> plaintext, Span<byte> destination)
    {
        CheckLengths(plaintext, destination);
        for (int i = 0; i < plaintext.Length; i += BlockSize)
            EncryptBlock(plaintext.Slice(i, BlockSize), destination.Slice(i, BlockSize));
    }

    public void DecryptEcb(ReadOnlySpan<byte> ciphertext, Span<byte> destination)
    {
        CheckLengths(ciphertext, destination);
        for (int i = 0; i < ciphertext.Length; i += BlockSize)
            DecryptBlock(ciphertext.Slice(i, BlockSize), destination.Slice(i, BlockSize));
    }

    public void EncryptCbc(ReadOnlySpan<byte> plaintext, Span<byte> destination)
    {
        CheckLengths(plaintext, destination);
        Span<byte> prev = stackalloc byte[BlockSize];
        Span<byte> block = stackalloc byte[BlockSize];
        _iv.CopyTo(prev);
        for (int i = 0; i < plaintext.Length; i += BlockSize)
        {
            for (int j = 0; j < BlockSize; j++)
                block[j] = (byte)(plaintext[i + j] ^ prev[j]);
            var output = destination.Slice(i, BlockSize);
            EncryptBlock(block, output);
            output.CopyTo(prev);
        }
    }

    public void DecryptCbc(ReadOnlySpan<byte> ciphertext, Span<byte> destination)
    {
        CheckLengths(ciphertext, destination);
        Span<byte> prev = stackalloc byte[BlockSize];
        Span<byte> current = stackalloc byte[BlockSize];
        _iv.CopyTo(prev);
        for (int i = 0; i < ciphertext.Length; i += BlockSize)
        {
            // Copy first so in-place decryption (same source and destination) still works.
            ciphertext.Slice(i, BlockSize).CopyTo(current);
            var output = destination.Slice(i, BlockSize);
            DecryptBlock(current, output);
            for (int j = 0; j < BlockSize; j++)
                output[j] ^= prev[j];
            current.CopyTo(prev);
        }
    }

    private static void CheckLengths(ReadOnlySpan<byte> input, Span<byte> destination)
    {
        if (input.Length % BlockSize != 0)
            throw new ArgumentException("Input must be a multiple of the AES block size.");
        if (destination.Length < input.Length)
            throw new ArgumentException("Destination is too small.");
    }

    // ---- Block cipher (FIPS-197) ----

    private static readonly byte[] SBox = BuildSBox(out InvSBox);
    private static readonly byte[] InvSBox;

    private static byte[] BuildSBox(out byte[] inverse)
    {
        var sbox = new byte[256];
        inverse = new byte[256];
        byte p = 1, q = 1;
        // Walk the multiplicative group with generator 3, tracking its inverse alongside.
        do
        {
            p = (byte)(p ^ (p << 1) ^ ((p & 0x80) != 0 ? 0x1B : 0));
            q ^= (byte)(q << 1);
            q ^= (byte)(q << 2);
            q ^= (byte)(q << 4);
            if ((q & 0x80) != 0)
                q ^= 0x09;
            byte x = (byte)(q ^ Rotl8(q, 1) ^ Rotl8(q, 2) ^ Rotl8(q, 3) ^ Rotl8(q, 4) ^ 0x63);
            sbox[p] = x;
        } while (p != 1);
        sbox[0] = 0x63;
        for (int i = 0; i < 256; i++)
            inverse[sbox[i]] = (byte)i;
        return sbox;
    }

    private static byte Rotl8(byte x, int shift) => (byte)((x << shift) | (x >> (8 - shift)));

    private static byte XTime(byte b) => (byte)((b << 1) ^ ((b & 0x80) != 0 ? 0x1B : 0));

    private static byte Mul(byte a, byte b)
    {
        byte result = 0;
        while (b != 0)
        {
            if ((b & 1) != 0)
                result ^= a;
            a = XTime(a);
            b >>= 1;
        }
        return result;
    }

    private static uint SubWord(uint w)
        => (uint)(SBox[w >> 24] << 24 | SBox[(w >> 16) & 0xFF] << 16 | SBox[(w >> 8) & 0xFF] << 8 | SBox[w & 0xFF]);

    private static uint[] ExpandKey(byte[] key, int rounds)
    {
        int nk = key.Length / 4;
        var w = new uint[4 * (rounds + 1)];
        for (int i = 0; i < nk; i++)
            w[i] = (uint)(key[4 * i] << 24 | key[(4 * i) + 1] << 16 | key[(4 * i) + 2] << 8 | key[(4 * i) + 3]);

        byte rcon = 1;
        for (int i = nk; i < w.Length; i++)
        {
            uint temp = w[i - 1];
            if (i % nk == 0)
            {
                temp = SubWord((temp << 8) | (temp >> 24)) ^ ((uint)rcon << 24);
                rcon = XTime(rcon);
            }
            else if (nk > 6 && i % nk == 4)
            {
                temp = SubWord(temp);
            }
            w[i] = w[i - nk] ^ temp;
        }
        return w;
    }

    private void EncryptBlock(ReadOnlySpan<byte> input, Span<byte> output)
    {
        Span<byte> s = stackalloc byte[BlockSize];
        input.CopyTo(s);
        AddRoundKey(s, _keys, 0);
        for (int round = 1; round < _rounds; round++)
        {
            SubBytes(s, SBox);
            ShiftRows(s);
            MixColumns(s);
            AddRoundKey(s, _keys, round);
        }
        SubBytes(s, SBox);
        ShiftRows(s);
        AddRoundKey(s, _keys, _rounds);
        s.CopyTo(output);
    }

    // The straightforward inverse cipher walks the same key schedule backwards.
    private void DecryptBlock(ReadOnlySpan<byte> input, Span<byte> output)
    {
        Span<byte> s = stackalloc byte[BlockSize];
        input.CopyTo(s);
        AddRoundKey(s, _keys, _rounds);
        for (int round = _rounds - 1; round > 0; round--)
        {
            InvShiftRows(s);
            SubBytes(s, InvSBox);
            AddRoundKey(s, _keys, round);
            InvMixColumns(s);
        }
        InvShiftRows(s);
        SubBytes(s, InvSBox);
        AddRoundKey(s, _keys, 0);
        s.CopyTo(output);
    }

    // State is column-major: s[4 * col + row], matching the input byte order.
    private static void AddRoundKey(Span<byte> s, uint[] keys, int round)
    {
        for (int c = 0; c < 4; c++)
        {
            uint k = keys[(round * 4) + c];
            s[4 * c] ^= (byte)(k >> 24);
            s[(4 * c) + 1] ^= (byte)(k >> 16);
            s[(4 * c) + 2] ^= (byte)(k >> 8);
            s[(4 * c) + 3] ^= (byte)k;
        }
    }

    private static void SubBytes(Span<byte> s, byte[] box)
    {
        for (int i = 0; i < BlockSize; i++)
            s[i] = box[s[i]];
    }

    private static void ShiftRows(Span<byte> s)
    {
        Span<byte> t = stackalloc byte[BlockSize];
        for (int c = 0; c < 4; c++)
        {
            for (int r = 0; r < 4; r++)
                t[(4 * c) + r] = s[(4 * ((c + r) % 4)) + r];
        }
        t.CopyTo(s);
    }

    private static void InvShiftRows(Span<byte> s)
    {
        Span<byte> t = stackalloc byte[BlockSize];
        for (int c = 0; c < 4; c++)
        {
            for (int r = 0; r < 4; r++)
                t[(4 * ((c + r) % 4)) + r] = s[(4 * c) + r];
        }
        t.CopyTo(s);
    }

    private static void MixColumns(Span<byte> s)
    {
        for (int c = 0; c < 4; c++)
        {
            int i = 4 * c;
            byte a0 = s[i], a1 = s[i + 1], a2 = s[i + 2], a3 = s[i + 3];
            s[i] = (byte)(XTime(a0) ^ XTime(a1) ^ a1 ^ a2 ^ a3);
            s[i + 1] = (byte)(a0 ^ XTime(a1) ^ XTime(a2) ^ a2 ^ a3);
            s[i + 2] = (byte)(a0 ^ a1 ^ XTime(a2) ^ XTime(a3) ^ a3);
            s[i + 3] = (byte)(XTime(a0) ^ a0 ^ a1 ^ a2 ^ XTime(a3));
        }
    }

    private static void InvMixColumns(Span<byte> s)
    {
        for (int c = 0; c < 4; c++)
        {
            int i = 4 * c;
            byte a0 = s[i], a1 = s[i + 1], a2 = s[i + 2], a3 = s[i + 3];
            s[i] = (byte)(Mul(a0, 14) ^ Mul(a1, 11) ^ Mul(a2, 13) ^ Mul(a3, 9));
            s[i + 1] = (byte)(Mul(a0, 9) ^ Mul(a1, 14) ^ Mul(a2, 11) ^ Mul(a3, 13));
            s[i + 2] = (byte)(Mul(a0, 13) ^ Mul(a1, 9) ^ Mul(a2, 14) ^ Mul(a3, 11));
            s[i + 3] = (byte)(Mul(a0, 11) ^ Mul(a1, 13) ^ Mul(a2, 9) ^ Mul(a3, 14));
        }
    }
}
