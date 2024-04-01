document.addEventListener('DOMContentLoaded', function() {
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // Listen for form submission
  document.querySelector('#compose-form').onsubmit = function(event) {
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
          if (result.message) {
            alert(result.message); // Display success message
            load_mailbox('sent');  // Load the sent mailbox
          } else {
              // Display an error message if the email wasn't sent
              alert(result.error);
          }
      });

      // Prevent form from submitting
      return false;
  };
});

function compose_email(email = null) {
    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    if (email) {
        // Pre-fill the form with the original email's details
        document.querySelector('#compose-recipients').value = email.sender;
        document.querySelector('#compose-subject').value = email.subject.startsWith('Re: ') ? email.subject : `Re: ${email.subject}`;
        document.querySelector('#compose-body').value = `\n\nOn ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
    } else {
        // Clear out composition fields
        document.querySelector('#compose-recipients').value = '';
        document.querySelector('#compose-subject').value = '';
        document.querySelector('#compose-body').value = '';
    }
  }


function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch and display emails for the mailbox
  fetch(`/emails/${mailbox}`)
      .then(response => response.json())
      .then(emails => {
          // Iterate over emails and create HTML elements to display them
          emails.forEach(email => {
              const emailElement = document.createElement('div');
              emailElement.className = `email-box ${email.read ? 'read' : 'unread'}`;
              emailElement.style.backgroundColor = email.read ? '#f8f9fa' : 'white';
              emailElement.innerHTML = `
                  <div>From: ${email.sender}</div>
                  <div class="email-subject" data-email-id="${email.id}">Subject: ${email.subject}</div>
                  <div>Timestamp: ${email.timestamp}</div>
              `;
              document.querySelector('#emails-view').appendChild(emailElement);
          });
          // Add event listeners to each subject line
          document.querySelectorAll('.email-subject').forEach(subject => {
            subject.addEventListener('click', function() {
                view_email(this.getAttribute('data-email-id'));
            });
        });
    });
}

function view_email(email_id, mailbox) {
// Fetch and display the full email
fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
        // Show the email details
        document.querySelector('#emails-view').innerHTML = `
            <div><strong>From:</strong> ${email.sender}</div>
            <div><strong>To:</strong> ${email.recipients.join(', ')}</div>
            <div><strong>Subject:</strong> ${email.subject}</div>
            <div><strong>Timestamp:</strong> ${email.timestamp}</div>
            <hr>
            <div>${email.body}</div>
          `;

          // Add a "Reply" button
          const replyButton = document.createElement('button');
          replyButton.textContent = 'Reply';
          replyButton.addEventListener('click', () => compose_email(email));
          document.querySelector('#emails-view').appendChild(replyButton);

          // Add an "Archive/Unarchive" button if not viewing a sent email
          if (mailbox !== 'sent') {
            const archiveButton = document.createElement('button');
            archiveButton.textContent = email.archived ? 'Unarchive' : 'Archive';
            archiveButton.addEventListener('click', () => {
                fetch(`/emails/${email_id}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        archived: !email.archived
                    })
                })
                .then(() => {
                    load_mailbox('inbox');
                });
            });
            document.querySelector('#emails-view').appendChild(archiveButton);
        }
    });
}
