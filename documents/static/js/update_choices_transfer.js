document.body.addEventListener('change', function (event) {
    let id = (event.target.id).split('-')[1];
    const re_location = new RegExp("^id_products-[0-9]*-location$");
    const id_warehouse = 'id_warehouse';
    const id_location = "#id_products-" + id + "-location";
    const id_lot_number = "#id_products-" + id + "-lot_number";


    if(event.target.id === id_warehouse){
        var url = $("#documentForm").attr("warehouse-url");
        var warehouseId = $('#id_warehouse').val();
        $('.quantity_information').html("<span style=\"line-height: 38px;\">-</span>")

        $.ajax({
            url: url,
            data: {
                'warehouse': warehouseId
            },
            success: function (data) {
                $('.product-select').html(data);
                $('.location-select').html('<option value="">---------</option>');
            }
        });
    }

    if (re_location.test(event.target.id)){
        const location_id = "#" + event.target.id;
        let location = $(location_id);
        let quantity = $("option:selected", location).attr("quantity");
        let quantity_td = $(location).closest("td").next();
        quantity_td.html("<span style=\"line-height: 38px;\">" + quantity.toString() + " szt." + "</span>");
        let lot_number = $("option:selected", location).attr("lot_number");
        $(id_lot_number).val(lot_number);
    }

    if (event.target.id === 'id_target_warehouse') {
        let url = $("#documentForm").attr("location-target-url");
        let warehouseId = $('#id_target_warehouse').val();

        $.ajax({
            url: url,
            data: {
                'target-warehouse': warehouseId
            },
            success: function (data) {
                $('.location-target-select').html(data);
            }
        });
    }
});

$(document.body).on("change", ".select2-field", function (){
    const re_product = new RegExp("^id_products-[0-9]*-product$");
    let id = (this.id).split('-')[1];
    const id_location = "#id_products-" + id + "-location";
    const id_product = "#" + this.id;

    if (re_product.test(this.id)){
        var url = $("#documentForm").attr("product-url");
        var productId = $(id_product).val();
        var warehouseId = $('#id_warehouse').val();

        $.ajax({
            url: url,
            data: {
                'product': productId,
                'warehouse_product': warehouseId,
            },
            success: function (data) {
                $(id_location).html(data)
            }
        });
    }
});