document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="number"]');
    
    inputs.forEach(input => {
        const label = input.previousElementSibling;
        if (label && label.htmlFor === input.id) {
            const mdInput = document.createElement('md-outlined-text-field');
            mdInput.label = label.textContent.trim();
            mdInput.name = input.name;
            mdInput.value = input.value;
            mdInput.type = input.type;
            if (input.required) mdInput.required = true;
            if (input.readOnly) mdInput.readOnly = true;
            if (input.disabled) mdInput.disabled = true;
            
            label.parentNode.replaceChild(mdInput, label);
            input.remove();
        }
    });
});
