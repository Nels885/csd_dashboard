        function partList() {
            $.ajax({
                type: "GET",
                url: PART_LIST_URL,
                success: function (res) {
                    let partListElement = document.getElementById('part-list');
                    partListElement.innerHTML = "";
                    for (const row of res.data) {
                        partListElement.innerHTML += `
                            <div class="form-group row">
                                <label for="form-product_code" class="col-sm-2 col-form-label">Code produit</label>
                                <div class="col-sm-3">
                                    <input type="text" class="form-control" id="form-product_code" value="${row.product_code}" readonly>
                                </div>

                                <label for="form-quantity" class="col-sm-2 col-form-label">Quantité</label>
                                <div class="col-sm-1">
                                    <input type="text" class="form-control" id="form-quantity" value="${row.quantity}" readonly>
                                </div>

                                <div class="col-sm-1">
                                    <button type="button" onclick="removeRow(${row.id})" class="btn btn-danger" title="Suppression pièce détachée">
                                        <i class="fas fa-trash-alt"></i>
                                    </button>
                                </div>
                            </div>
                        `;
                    }
                }
            });
        }

        function removeRow(part_id) {
            console.log("Test OK")
            console.log(part_id);
            if (confirm("Voulez-vous supprimer cette pièce ?")) {
                $.ajax({
                    type: "GET",
                    url: `/reman/repair-part/${part_id}/delete/ajax/`,
                    success: function (res) {
                        // console.log(res);
                        partList();
                    },
                    error: function (err) {
                        console.log(err);
                    }
                });
            }
        }
