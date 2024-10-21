

function toggleDetails(resultId) {
    const detailsRow = document.getElementById('details-' + resultId);
    if (detailsRow.style.display === "none") {
        detailsRow.style.display = "table-row";
    } else {
        detailsRow.style.display = "none";
    }
}
