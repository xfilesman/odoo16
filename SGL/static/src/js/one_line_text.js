/** @odoo-module **/

// Prevent multi-line input and Enter key for fields marked with .sgl-one-line
(function initOneLineText() {
    const addGuards = () => {
        const keydownHandler = (e) => {
            const t = e.target;
            if (t && t.closest && t.closest('.sgl-one-line') && t.tagName === 'TEXTAREA') {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        };

        const inputHandler = (e) => {
            const t = e.target;
            if (t && t.closest && t.closest('.sgl-one-line') && t.tagName === 'TEXTAREA') {
                if (t.value && t.value.indexOf('\n') !== -1) {
                    t.value = t.value.replace(/\n/g, ' ');
                }
            }
        };

        document.addEventListener('keydown', keydownHandler, true);
        document.addEventListener('input', inputHandler, true);

        // Force Shipment Description to be one-line height and aligned
        const applyShipmentDescriptionFix = () => {
            const areas = document.querySelectorAll('textarea[name="shipment_description"]');
            areas.forEach((t) => {
                try {
                    t.style.height = '38px';
                    t.style.minHeight = '38px';
                    t.style.maxHeight = '38px';
                    t.style.lineHeight = '22px';
                    t.style.overflow = 'hidden';
                    t.style.whiteSpace = 'nowrap';
                    t.style.textOverflow = 'ellipsis';
                    t.style.resize = 'none';
                } catch (_) {}
            });
        };

        // Initial apply
        applyShipmentDescriptionFix();
        // Re-apply on DOM changes (form rerenders)
        const mo = new MutationObserver(() => applyShipmentDescriptionFix());
        if (document.body) {
            mo.observe(document.body, { childList: true, subtree: true });
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addGuards);
    } else {
        addGuards();
    }
})();


