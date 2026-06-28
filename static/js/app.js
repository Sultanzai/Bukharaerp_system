// document.addEventListener('DOMContentLoaded', function () {

//     const toggle = document.getElementById('menuToggle');
//     const sidebar = document.getElementById('sidebar');

//     toggle.addEventListener('click', function () {

//         sidebar.classList.toggle('d-none');

//     });

// });

// $(function () {
//     $('.datatable').DataTable({
//         responsive: true,
//         pageLength: 10,
//         autoWidth: false,
//         order: [[0, 'desc']]
//     });
// });


console.log("app.js loaded");




document.addEventListener('DOMContentLoaded', function () {

    const toggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (toggle && sidebar) {

        toggle.addEventListener('click', function () {

            sidebar.classList.toggle('d-none');

        });

    }

});


$(document).ready(function () {

    if ($.fn.DataTable) {

        $('.datatable').DataTable({

            responsive: true,

            autoWidth: false,

            pageLength: 10,

            lengthMenu: [
                [10, 25, 50, 100],
                [10, 25, 50, 100]
            ],

            order: [[0, 'desc']],

            language: {

                search: "",

                searchPlaceholder: "Search...",

                lengthMenu: "Show _MENU_ entries",

                info: "Showing _START_ to _END_ of _TOTAL_ entries",

                zeroRecords: "No matching records found.",

                infoEmpty: "No records available."

            }

        });

    }

});