document.addEventListener("DOMContentLoaded", function() {
    const transactionTypeSelect = document.getElementById("id_transaction_type");
    const categorySelect = document.getElementById("id_category");
    const accountNameSelect = document.getElementById("id_account_name");
    const preAuthDateField = document.getElementById("id_pre_auth_date").closest(".form-group");

    // Object to cache fetched categories
    const categoryCache = {};

    function togglePreAuthDateVisibility() {
        const category = categorySelect.value;
        if (category === "Pre-Auth Payments") {
            preAuthDateField.classList.add('pre-auth-visible');
        } else {
            preAuthDateField.classList.remove('pre-auth-visible');
        }
    }    

    transactionTypeSelect.addEventListener("change", async function() {
        const transactionType = this.value;
    
        // Check if categories are cached
        if (categoryCache[transactionType]) {
            populateCategories(categoryCache[transactionType]);
        } else {
            // Fetch categories from the server
            try {
                const response = await fetch(`/get-categories/?transaction_type=${transactionType}`);
                if (response.ok) {
                    const categories = await response.json();
                    // Cache the fetched categories
                    categoryCache[transactionType] = categories;
                    populateCategories(categories);
                } else {
                    console.error('Failed to fetch categories');
                }
            } catch (error) {
                console.error('Error fetching categories:', error);
            }
        }
    
        // Call the function to toggle the visibility of the pre-auth date field
        togglePreAuthDateVisibility();
    });

    // Function to populate category options in the select element
    function populateCategories(categories) {
        // Clear existing options in the category select
        categorySelect.innerHTML = '';

        // Add a default option to add a new category
        const addNewOption = document.createElement("option");
        addNewOption.value = "";
        addNewOption.textContent = "--- Add New ---";
        categorySelect.appendChild(addNewOption);
        
        // Populate categories based on the fetched data
        categories.forEach(category => {
            const option = document.createElement("option");
            option.value = category.value;
            option.textContent = category.text;
            categorySelect.appendChild(option);
        });
    }

    categorySelect.addEventListener("change", togglePreAuthDateVisibility);

    accountNameSelect.addEventListener("change", async function() {
        if (this.value === "") {
            // Fetch account names from the server
            try {
                const response = await fetch('/get-account-names/');
                if (response.ok) {
                    const accountNames = await response.json();
    
                    // Clear existing options in the account name select
                    accountNameSelect.innerHTML = '';
    
                    // Add a default option to add a new account name
                    const addNewOption = document.createElement("option");
                    addNewOption.value = "";
                    addNewOption.textContent = "--- Add New ---";
                    accountNameSelect.appendChild(addNewOption);
                    
                    // Populate account names based on the fetched data
                    accountNames.forEach(accountName => {
                        const option = document.createElement("option");
                        option.value = accountName;
                        option.textContent = accountName;
                        accountNameSelect.appendChild(option);
                    });
    
                    // Prompt user to enter a new account name with error handling
                    let newAccountName = prompt("Enter new account name:");
                    while (newAccountName === "" || accountNames.includes(newAccountName)) {
                        newAccountName = prompt("Invalid or duplicate name. Enter a new account name:");
                        if (newAccountName === null) {
                            // User cancelled the prompt, reset the select to its default value
                            accountNameSelect.value = "";
                            return;
                        }
                    }
                    if (newAccountName) {
                        // Confirm before adding the new account name
                        if (confirm(`Are you sure you want to add "${newAccountName}" as a new account name?`)) {
                            // Add new account name to the dropdown
                            const newOption = document.createElement("option");
                            newOption.value = newAccountName;
                            newOption.textContent = newAccountName;
                            accountNameSelect.appendChild(newOption);
                            // Select the newly added option
                            accountNameSelect.value = newAccountName;
                            displaySuccessMessage('New account name added successfully.');
                            highlightNewOption(newOption);
                        } else {
                            // User cancelled the confirmation, reset the select to its default value
                            accountNameSelect.value = "";
                        }
                    }
                } else {
                    console.error('Failed to fetch account names');
                }
            } catch (error) {
                console.error('Error fetching account names:', error);
            }
        }
    });
    
    function displaySuccessMessage(message) {
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('success-message');
        messageContainer.textContent = message;
        document.body.appendChild(messageContainer);
    
        setTimeout(() => {
            messageContainer.remove();
        }, 3000); // Remove the message after 3 seconds
    }
    
    function highlightNewOption(option) {
        option.classList.add('highlight');
        setTimeout(() => {
            option.classList.remove('highlight');
        }, 3000); // Remove the highlight after 3 seconds
    }
    

    // Initialize form state
    togglePreAuthDateVisibility();
});

