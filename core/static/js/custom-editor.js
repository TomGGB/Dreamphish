document.addEventListener('DOMContentLoaded', function() {
    const editorIframe = document.getElementById('editor-iframe');
    const plainTextEditor = document.getElementById('plain-text-editor');
    const toolbar = document.querySelector('.toolbar');
    const hiddenTextarea = document.getElementById('id_body') || document.getElementById('id_html_content');
    const toggleEditorButton = document.getElementById('toggle-editor');
    const form = document.querySelector('form');
    let isHtmlMode = true;

    function getIframeDocument() {
        return editorIframe.contentDocument || editorIframe.contentWindow.document;
    }

    function updateHiddenTextarea() {
        hiddenTextarea.value = isHtmlMode ? getIframeDocument().body.innerHTML : plainTextEditor.value;
    }

    function toggleEditor() {
        isHtmlMode = !isHtmlMode;
        if (isHtmlMode) {
            getIframeDocument().body.innerHTML = plainTextEditor.value;
            editorIframe.style.display = 'block';
            plainTextEditor.style.display = 'none';
            toolbar.querySelectorAll('button:not(#toggle-editor)').forEach(btn => btn.disabled = false);
        } else {
            plainTextEditor.value = getIframeDocument().body.innerHTML;
            editorIframe.style.display = 'none';
            plainTextEditor.style.display = 'block';
            toolbar.querySelectorAll('button:not(#toggle-editor)').forEach(btn => btn.disabled = true);
        }
        toggleEditorButton.querySelector('i').textContent = isHtmlMode ? 'text_fields' : 'code';
        updateHiddenTextarea();
    }

    toggleEditorButton.addEventListener('click', toggleEditor);

    toolbar.addEventListener('click', function(e) {
        const command = e.target.closest('button')?.dataset.command;
        if (command && isHtmlMode) {
            e.preventDefault();
            getIframeDocument().execCommand(command, false, null);
            updateHiddenTextarea();
        }
    });

    // Inicializar el contenido del editor
    const initialContent = hiddenTextarea.value || '<p></p>';
    getIframeDocument().designMode = 'on';
    getIframeDocument().body.innerHTML = initialContent;
    updateHiddenTextarea();

    editorIframe.addEventListener('load', function() {
        getIframeDocument().body.addEventListener('input', updateHiddenTextarea);
    });

    // Manejar la inserción de chips (solo para plantillas de correo)
    const chipSet = document.querySelector('md-chip-set');
    if (chipSet) {
        chipSet.addEventListener('click', function(e) {
            const chip = e.target.closest('md-assist-chip');
            if (chip && isHtmlMode) {
                const value = chip.dataset.value;
                getIframeDocument().execCommand('insertText', false, value);
                updateHiddenTextarea();
            }
        });
    }

    // Actualizar el contenido antes de enviar el formulario
    form.addEventListener('submit', function(e) {
        updateHiddenTextarea();
    });
});
