document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}

document.addEventListener('DOMContentLoaded', function() {
  // Listen for form submission
  document.querySelector('#compose-form').onsubmit = function() {
      // Prevent default form submission
      event.preventDefault();

      // Get form data
      const recipients = document.querySelector('#compose-recipients').value;
      const subject = document.querySelector('#compose-subject').value;
      const body = document.querySelector('#compose-body').value;

      // Send POST request to /emails
      fetch('/emails', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
        },
          body: JSON.stringify({
              recipients: recipients,
              subject: subject,
              body: body
          })
      })
      .then(response => response.json())
      .then(result => {
          console.log(result); // For debugging
          // Check if the email was sent successfully
          if (result.message === "Email sent successfully.") {
              // Load the user's sent mailbox
              load_mailbox('sent');
          } else {
              // Display an error message if the email wasn't sent
              alert(result.error);
          }
      });

      // Prevent form from submitting
      return false;
  };
});
