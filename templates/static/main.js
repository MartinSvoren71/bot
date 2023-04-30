ClassicEditor
  .create(document.querySelector('#editor'), {
    toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote']
  })
  .then(editor => {
    console.log('Editor was initialized.', editor);
  })
  .catch(error => {
    console.error('There was a problem initializing the editor.', error);
  });
