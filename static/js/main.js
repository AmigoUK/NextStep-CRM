/* TradeFlow CRM — Delete confirmation modal handler */

document.addEventListener("DOMContentLoaded", function () {
    var deleteModal = document.getElementById("confirmDeleteModal");
    if (!deleteModal) return;

    deleteModal.addEventListener("show.bs.modal", function (event) {
        var button = event.relatedTarget;
        var itemName = button.getAttribute("data-item-name") || "this item";
        var deleteUrl = button.getAttribute("data-delete-url");

        document.getElementById("deleteItemName").textContent = itemName;
        document.getElementById("deleteForm").action = deleteUrl;
    });
});
