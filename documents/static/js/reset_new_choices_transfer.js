$(document).ready(function (){

    // Dodanie nowego formularza
    $('#add_product_btn').click(function (){
        // Zmienne z formset
        let last_form_id = $('#id_products-TOTAL_FORMS').val() - 1;
        const id_location = "#id_products-" + last_form_id + "-location";
        const id_product = "#id_products-" + last_form_id + "-product";
        const id_location_target = "#id_products-" + last_form_id + "-location_target";

        // Wszystkie pola select ustawione na 0
        $(id_location).prop('selectedIndex', 0);
        $(id_product).prop('selectedIndex', 0);
        $(id_location_target).prop('selectedIndex', 0);

        // Inicjalizacja klasy select2 dla nowego wyboru produktu
        $(document).ready(function (){
            $(".product_search").select2({placeholder: 'Wybierz produkt'});
            $(".location-target-select").select2({placeholder: 'Wybierz produkt'});
        });

        // Pobranie id magazynu do nowego formularza
        var url = $("#documentForm").attr("warehouse-url");
        var warehouseId = $('#id_warehouse').val();

        $.ajax({
            url: url,
            data: {
                'warehouse': warehouseId
            },
            success: function (data) {
                $(id_product).html(data)
            }
        });

        let url_target = $("#documentForm").attr("location-target-url");
        let warehouseId_target = $('#id_target_warehouse').val();

        $.ajax({
            url: url_target,
            data: {
                'target-warehouse': warehouseId_target
            },
            success: function (data) {
                $(id_location_target).html(data);
            }
        });

    });
})