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

    const importButton = document.getElementById('import-csv');
    const csvFileInput = document.getElementById('csv-file-input');

    importButton.addEventListener('click', function() {
        csvFileInput.click();  // Abre el diálogo de carga de archivos
    });

    csvFileInput.addEventListener('change', function() {
        // Aquí puedes manejar el archivo CSV seleccionado
        const file = csvFileInput.files[0];
        if (file) {
            // Puedes hacer algo con el archivo, como enviarlo a una vista
            console.log('Archivo seleccionado:', file.name);
        }
    });
});
