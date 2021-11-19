$(document).ready(function (){

    // Dodanie nowego formularza
    $('#add_product_btn').click(function (){

        // Zmienne z formset
        let last_form_id = $('#id_products-TOTAL_FORMS').val() - 1;
        const id_shelf = "#id_products-" + last_form_id + "-shelf";
        const id_location = "#id_products-" + last_form_id + "-location";
        const id_product = "#id_products-" + last_form_id + "-product";

        // Wszystkie pola select ustawione na 0
        $(id_location).prop('selectedIndex', 0);
        $(id_shelf).prop('selectedIndex', 0);
        $(id_product).prop('selectedIndex', 0);

        // Inicjalizacja klasy select2 dla nowego wyboru produktu
        $(document).ready(function (){
            $(".product_search").select2({placeholder: 'Wybierz produkt'});
        });

        // Pobranie id magazynu do nowego formularza
        var url = $("#documentForm").attr("data-url");
        var warehouseId = $('#id_warehouse').val();

        $.ajax({
            url: url,
            data: {
                'warehouse': warehouseId
            },
            success: function (data) {
                $(id_shelf).html(data)
            }
        });

    });
})