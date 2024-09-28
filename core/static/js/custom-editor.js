document.addEventListener('DOMContentLoaded', function() {
    const editorIframe = document.getElementById('editor-iframe');
    const plainTextEditor = document.getElementById('plain-text-editor');
    const toolbar = document.querySelector('.toolbar');
    const hiddenTextarea = document.getElementById('id_body') || document.getElementById('id_html_content');
    const toggleEditorButton = document.getElementById('toggle-editor');
    const form = document.querySelector('form');
    let isHtmlMode = false;

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
            toggleEditorButton.innerHTML = '<i class="material-icons">visibility</i> Modo Texto Plano';
        } else {
            plainTextEditor.value = getIframeDocument().body.innerHTML;
            editorIframe.style.display = 'none';
            plainTextEditor.style.display = 'block';
            toolbar.querySelectorAll('button:not(#toggle-editor)').forEach(btn => btn.disabled = true);
            toggleEditorButton.innerHTML = '<i class="material-icons">code</i> Modo HTML';
        }
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

    // Inicializar el contenido del editor en modo HTML
    const initialContent = hiddenTextarea.value || '';
    getIframeDocument().designMode = 'on';
    getIframeDocument().body.innerHTML = initialContent;
    editorIframe.style.display = 'none';
    plainTextEditor.style.display = 'block';
    isHtmlMode = false;
    toggleEditorButton.innerHTML = '<i class="material-icons">code</i> Modo HTML';

    // Asegurarse de que el contenido se cargue correctamente en el iframe
    editorIframe.addEventListener('load', function() {
        getIframeDocument().body.innerHTML = initialContent;
        getIframeDocument().body.addEventListener('input', updateHiddenTextarea);
    });

    // Habilitar los botones de la barra de herramientas
    toolbar.querySelectorAll('button:not(#toggle-editor)').forEach(btn => btn.disabled = false);

    // Manejar la inserción de chips (solo para plantillas de correo)
    const chipSet = document.querySelector('md-chip-set');
    if (chipSet) {
        chipSet.addEventListener('click', function(e) {
            const chip = e.target.closest('md-assist-chip');
            if (chip) {
                const value = chip.dataset.value;
                if (isHtmlMode) {
                    getIframeDocument().execCommand('insertText', false, value);
                } else {
                    insertTextAtCursor(plainTextEditor, value);
                }
                updateHiddenTextarea();
            }
        });
    }

    // Función para insertar texto en la posición del cursor
    function insertTextAtCursor(textarea, text) {
        const startPos = textarea.selectionStart;
        const endPos = textarea.selectionEnd;
        textarea.value = textarea.value.substring(0, startPos) + text + textarea.value.substring(endPos, textarea.value.length);
        textarea.selectionStart = textarea.selectionEnd = startPos + text.length;
    }

    // Actualizar el contenido antes de enviar el formulario
    form.addEventListener('submit', function(e) {
        updateHiddenTextarea();
    });
});
