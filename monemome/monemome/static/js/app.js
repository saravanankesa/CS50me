// File: static/js/app.js

// Common Utilities or Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Utility Functions for Dynamic UI Updates
function updateFormFields() {
    var transactionType = $('input[name="transaction_type"]:checked').val();
    $('.form-group').hide();
    $('.transaction-type').show();

    if (transactionType === 'Income') {
        $('.expense-only').hide();
        $('.income-only').show();
    } else if (transactionType === 'Expense') {
        $('.income-only').hide();
        $('.expense-only').show();
    }

    $('.common-fields').show();
    loadCategories(transactionType);
}

function loadCategories(transactionType) {
    $.ajax({
        url: `/api/categories/${transactionType}/`,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            var $categorySelect = $('#id_category');
            $categorySelect.empty();

            if (data.length === 0) {
                $categorySelect.html('<option>No categories available</option>');
            } else {
                $.each(data, function(i, cat) {
                    $categorySelect.append(new Option(cat.category_name, cat.id));
                });
            }

            $categorySelect.show();
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('Error loading categories:', errorThrown);
            $('#category-error').text('Failed to load categories. Please try again.');
        }
    });
}

// Document Ready Event Handler
$(document).ready(function() {
    // Handle close button actions for alerts
    $('.btn-close').click(function(event) {
        event.preventDefault();  // Prevent the default close behavior until the server is notified
        var $alert = $(this).closest('.alert');  // Get the parent alert of the close button
        
        $.ajax({
            url: '/dismiss-warning/',
            type: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function() {
                $alert.hide(); // Hide the alert if server processes dismissal successfully
                console.log('Warning dismissed');
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    });

    // Initialize all tooltips
    $('[data-bs-toggle="tooltip"]').tooltip(); 

    // Initialize Charts if corresponding elements exist
    if ($('#expenseChart').length && $('#incomeChart').length) {
        var expenseData = JSON.parse($('#expense-data').text());
        var incomeData = JSON.parse($('#income-data').text());

        var ctxExpense = $('#expenseChart').get(0).getContext('2d');
        var expenseChart = new Chart(ctxExpense, {
            type: 'pie',
            data: {
                labels: expenseData.map(data => data.name),
                datasets: [{
                    label: 'Expense Breakdown',
                    data: expenseData.map(data => data.value),
                    backgroundColor: ['#FFB280', '#FF7043', '#FF8966', '#FF6347', '#D85F52'], // Define colors
                    borderColor: '#94453d',  // Define border color
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, 
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            font: {
                                size: 16 
                            },
                            color: '#0e3821'
                        }
                    },
                }
            }
        });

        var ctxIncome = $('#incomeChart').get(0).getContext('2d');
        var incomeChart = new Chart(ctxIncome, {
            type: 'pie',
            data: {
                labels: incomeData.map(data => data.name),
                datasets: [{
                    label: 'Income Breakdown',
                    data: incomeData.map(data => data.value),
                    backgroundColor: ['#FFCC99', '#FF6600', '#FF7F50', '#FF4500', '#CC5500'], // Define colors
                    borderColor: '#94453d',  // Define border color
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            fontSize: 16,
                            fontColor: '#0e3821',
                            fontFamily: '"Lucida Console", Monaco, monospace'
                        }
                    },
                }
            }
        });
    }

    // Check if form container exists for add_transaction page
    if ($('#form-container').length) {
        $('#form-container p').each(function() {
            var $div = $('<div>').addClass('form-group').html($(this).html());
            var $input = $(this).find('input, select');
    
            if ($input.length) {
                $div.attr('id', 'div_' + $input.attr('name'));
                if ($input.attr('name') === 'is_pre_auth') {
                    $div.addClass('expense-only');
                } else if ($input.attr('name') === 'is_recurring') {
                    $div.addClass('income-only');
                }
            }
    
            $(this).replaceWith($div);
        });
    
        var $categorySelect = $('select[name="category"]');
        if ($categorySelect.length) {
            $('<p>').attr('id', 'category-error').addClass('text-danger').insertAfter($categorySelect);
        }
    
        $('input[name="transaction_type"]').change(function() {
            updateFormFields();
            loadCategories($(this).val());
        });
    
        if ($('input[name="transaction_type"]:checked').length) {
            updateFormFields();
            loadCategories($('input[name="transaction_type"]:checked').val());
        }
    }
    // Add more sections as necessary for each part of your app
});
