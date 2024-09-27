document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-form');
    const formsetContainer = document.getElementById('formset');
    const totalForms = document.getElementById('id_targets-TOTAL_FORMS');

    addButton.addEventListener('click', function() {
        const formCount = formsetContainer.children.length;
        const newForm = formsetContainer.children[0].cloneNode(true);
        const formRegex = RegExp(`targets-(\\d+)-`,'g');

        newForm.innerHTML = newForm.innerHTML.replace(formRegex, `targets-${formCount}-`);
        formsetContainer.appendChild(newForm);

        totalForms.setAttribute('value', formCount + 1);
    });
});
