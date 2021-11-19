document.body.addEventListener('change', function (event) {
    const re_shelf = new RegExp("^(id_products-[0-9]*-shelf)$");
    let id = (event.target.id).split('-')[1];

    const id_shelf = "#id_products-" + id + "-shelf";
    const id_location = "#id_products-" + id + "-location";
    const id_warehouse = 'id_warehouse';

    if(event.target.id === id_warehouse){
        var url = $("#documentForm").attr("data-url");
        var warehouseId = $('#id_warehouse').val();

        $.ajax({
            url: url,
            data: {
                'warehouse': warehouseId
            },
            success: function (data) {
                $('.shelf-select').html(data)
                $('.location-select').html('<option value="">---------</option>')
            }
        });

        if(warehouseId === ''){
            $('.shelf-select').prop('selectedIndex', 0);
            $('.shelf-select').html('<option value="">---------</option>');

            $('.location-select').prop('selectedIndex', 0);
            $('.location-select').html('<option value="">---------</option>');
        }

        $('.location-select').prop('selectedIndex', 0);
    }

    if(re_shelf.test(event.target.id)) {
        url = $("#documentForm").attr("location-url");
        var shelfId = $(id_shelf).val();

        $.ajax({
            url: url,
            data: {
                'shelf': shelfId
            },
            success: function (data) {
                $(id_location).html(data)
            }
        });

        if(shelfId === ''){
            $(id_location).prop('selectedIndex', 0);
            $(id_location).html('<option value="">---------</option>');
        }
    }
});