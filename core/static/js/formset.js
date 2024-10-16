document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-form');
    const formsetContainer = document.getElementById('formset');
    const totalForms = document.getElementById('id_targets-TOTAL_FORMS');

    if (addButton) {
        addButton.addEventListener('click', function() {
            const formCount = formsetContainer.children.length;
            const newForm = formsetContainer.children[0].cloneNode(true);
            const formRegex = RegExp(`targets-(\\d+)-`,'g');

            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `targets-${formCount}-`);
            formsetContainer.appendChild(newForm);

            totalForms.setAttribute('value', formCount + 1);
        });
    }

    const importButton = document.getElementById('import-csv');
    const csvFileInput = document.getElementById('csv-file-input');

    if (importButton && csvFileInput) {
        importButton.addEventListener('click', function() {
            csvFileInput.click();
        });

        csvFileInput.addEventListener('change', function() {
            const file = csvFileInput.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('csv_file', file);
                formData.append('group_name', prompt('Ingrese el nombre del grupo:'));

                fetch('/groups/import_csv/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Importación exitosa');
                        window.location.href = '/groups/'; // Redirigir a /groups/ después de la importación exitosa
                    } else {
                        alert('Error en la importación: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error en la importación');
                });
            }
        });
    }
});
