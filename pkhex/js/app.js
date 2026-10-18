// Helpers called from Blazor through JS interop.
window.pkhex = {
    // Hands the edited save back to the user. On iOS the share sheet is the reliable way to
    // put a file into the Files app (and from there into the emulator's folder).
    async saveFile(fileName, bytes) {
        const file = new File([bytes], fileName, { type: 'application/octet-stream' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
            try {
                await navigator.share({ files: [file] });
                return 'shared';
            } catch (e) {
                if (e && e.name === 'AbortError')
                    return 'cancelled';
                // Fall through to a plain download.
            }
        }
        const url = URL.createObjectURL(file);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 10000);
        return 'downloaded';
    },

    // Warn before leaving with unsaved edits.
    setDirty(dirty) {
        window.onbeforeunload = dirty ? (e) => { e.preventDefault(); return ''; } : null;
    },

    scrollTop() {
        window.scrollTo(0, 0);
    },

    focus(element) {
        if (element) element.focus();
    },
};
