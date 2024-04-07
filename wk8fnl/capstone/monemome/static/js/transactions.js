document.addEventListener("DOMContentLoaded", function() {
    const transactionTypeSelect = document.getElementById("id_transaction_type");
    const categorySelect = document.getElementById("id_category");
    const newCategoryField = document.getElementById("id_new_category");
    const addCategoryButton = document.getElementById("add_category_button");
    const preAuthCheckbox = document.getElementById("id_pre_auth");
    const preAuthDateField = document.getElementById("id_pre_auth_date").closest(".form-group");
    const accountNameSelect = document.getElementById("id_account_name");
    const newAccountNameField = document.getElementById("id_new_account_name");
    const addAccountButton = document.getElementById("add_account_button");

    function togglePreAuthDateVisibility() {
        if (preAuthCheckbox.checked) {
            preAuthDateField.style.display = 'block';
        } else {
            preAuthDateField.style.display = 'none';
        }
    }    

    function populateAccountNames() {
        accountNames.forEach(name => {
            const option = document.createElement("option");
            option.value = name;
            option.textContent = name;
            accountNameSelect.appendChild(option);
        });
    }

    // Call the populateAccountNames function to fill the dropdown
    populateAccountNames();

    function updateCategoryOptions(transactionType) {
        // Fetch categories from the server based on the transaction type
        fetch(`/get-categories/?transaction_type=${transactionType}`)
            .then(response => response.json())
            .then(data => {
                // Clear existing options
                categorySelect.innerHTML = '';
                // Add new options
                data.categories.forEach(category => {
                    const option = document.createElement("option");
                    option.value = category;
                    option.textContent = category;
                    categorySelect.appendChild(option);
                });
            });
    }

    function addNewAccount() {
        const newAccountName = newAccountNameField.value.trim();
        if (newAccountName) {
            // Add the new account name to the accountNameSelect
            const option = document.createElement("option");
            option.value = newAccountName;
            option.textContent = newAccountName;
            accountNameSelect.appendChild(option);
            // Select the newly added option
            accountNameSelect.value = newAccountName;
            // Clear the newAccountNameField
            newAccountNameField.value = '';
        }
    }

    function addNewCategory() {
        const newCategory = newCategoryField.value.trim();
        if (newCategory) {
            // Add the new category to the categorySelect
            const option = document.createElement("option");
            option.value = newCategory;
            option.textContent = newCategory;
            categorySelect.appendChild(option);
            // Select the newly added option
            categorySelect.value = newCategory;
            // Clear the newCategoryField
            newCategoryField.value = '';
        }
    }

    transactionTypeSelect.addEventListener("change", function() {
        updateCategoryOptions(this.value);
        togglePreAuthDateVisibility();
    });

    preAuthCheckbox.addEventListener("change", togglePreAuthDateVisibility);

    addAccountButton.addEventListener("click", addNewAccount);
    addCategoryButton.addEventListener("click", addNewCategory);

    // Initial setup
    togglePreAuthDateVisibility();
    updateCategoryOptions(transactionTypeSelect.value);
});

   