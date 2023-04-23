    function openPdf(presignedUrl) {
      console.log('Presigned URL:', presignedUrl);
      let pdfEmbed = document.getElementById('pdf-embed');
      pdfEmbed.setAttribute('src', presignedUrl);
      }
      
      
      function loadLogFile() {
      const logContainer = document.getElementById('log-container');
      
      fetch('/log-content')
      .then(response => response.text())
      .then(data => {
      logContainer.innerHTML = data;
      })
      .catch(error => {
      console.error('Error fetching log.txt:', error);
      });
      }
      
      loadLogFile();
             
      
       function saveFolderx() {
       const saveFolder = document.getElementById("folder-select").value;
       localStorage.setItem("folder-select", saveFolder);
      }  
       
          
       
      async function ask_LIB(event) {
                  //  wait();
         wait2();
         event.preventDefault();
        const form = document.getElementById("ask-form");
        const formData = new FormData(form);
        const response =  fetch("/ask_lib", {
            method: "POST",
            body: formData,
        });
      } 
       async function ask_GPT(event) {
                    // wait();
      wait2();
        event.preventDefault();   
        const form = document.getElementById("ask-form");
        const formData = new FormData(form);
        const response =  fetch("/ask_gpt", {
            method: "POST",
            body: formData,
        });     
       }  
       
       
      async function save(event) {
      event.preventDefault();
      
      // Extract the HTML content from the Quill editor
      const content = quill.root.innerHTML;
      
      // Create a new div element and set its innerHTML to the extracted content
      const contentDiv = document.createElement('div');
      contentDiv.innerHTML = content;
      
      // Render the content div using html2canvas with an increased scale factor
      const scale = 3; // Increase the scale factor to improve resolution
      const canvas = await html2canvas(contentDiv, { scale });
      
      // Create a new jsPDF instance
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      // Add the rendered canvas to the PDF
      const imgData = canvas.toDataURL('image/png');
      const imgProps = pdf.getImageProperties(imgData);
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      
      // Download the PDF
      pdf.save('download.pdf');
      }
      
       
      
       
      function searchFiles() {
      searchFiles_1();
          wait();
      let keyword = $('#keyword').val();
      let selectedFolder = $('#folder-selector').val();
      console.log("Sending data:", { keyword: keyword, folder_path: selectedFolder }); // Add this line
      $.post('/search_pdf_files', { keyword: keyword, folder_path: selectedFolder }, function (data) {
        $('#search-results').html(data.rendered_template);
        loader.style.display = "none";
      });
      }
      
      function searchFiles_1() {
      const keyword = $('#keyword').val();
      $.ajax({
        url: '/search_pdf_files',
        method: 'POST',
        data: {
            keyword: keyword,
        },
        success: function(data) {
            // Render the search results
            $('.results').html(data.rendered_template);
        },
        error: function(err) {
            console.log(err);
        }
      });
      }
       
       
      function showPDF(url) {
      document.getElementById('pdf-embed').src = '/lurl.pdf';
      setTimeout(() => {
        document.getElementById('pdf-embed').src = url;
      }, 300);
      }
       
        const canvas = document.getElementById('matrixCanvas');
         const ctx = canvas.getContext('2d');
         canvas.width = window.innerWidth;
         canvas.height = window.innerHeight;
         
      const characters = '゠ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヷヸヹヺ・ーヽヾゝゞー１２３４５６７８９０';
         
         const fontSize = 15;
         const columns = canvas.width / fontSize;
         
         const drops = [];
         for (let i = 0; i < columns; i++) {
         	drops[i] = 1;
         }
         
         function draw() {
         	ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
         	ctx.fillRect(0, 0, canvas.width, canvas.height);
         
         	ctx.fillStyle = '#a36e0a';
         	ctx.font = `${fontSize}px monospace`;
         
         	for (let i = 0; i < drops.length; i++) {
         		const text = characters.charAt(Math.floor(Math.random() * characters.length));
         		ctx.fillText(text, i * fontSize, drops[i] * fontSize);
         
         		if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
         			drops[i] = 0;
         		}
         		drops[i]++;
         	}
         }
         
         setInterval(draw, 33);
       
      // Initialize Quill editor
      var quill = new Quill('#quill-editor', {
      theme: 'snow'
      });
      
      async function save_doc() {
      // Get content from Quill editor
      const content = quill.root.innerHTML;
      
      // Create a temporary container for rendering
      const container = document.createElement('div');
      container.innerHTML = content;
      container.style.width = '8.5in';
      container.style.height = '11in';
      container.style.overflow = 'hidden';
      container.style.position = 'absolute';
      container.style.left = '-9999px';
      container.style.top = '-9999px';
      document.body.appendChild(container);
      
      // Render the content as an image using html2canvas
      const canvas = await html2canvas(container, { scale: 0.72 });
      
      // Remove the temporary container
      document.body.removeChild(container);
      
      // Convert the canvas to a data URL
      const imageDataUrl = canvas.toDataURL('image/png');
      
      // Get the current date and time
      const now = new Date();
      const dateString = now.toLocaleDateString();
      const timeString = now.toLocaleTimeString();
      
      // Define the PDF content using pdfmake
      const docDefinition = {
      header: {
      text: `generated by KV ${dateString} ${timeString}`,
      margin: [20, 20, 20, 20],
      style: 'header',
      },
      content: [
      {
        image: imageDataUrl,
        width: canvas.width * 0.85,
        height: canvas.height * 0.85,
      },
      {
      
      },
        {
      
      },
      ],
      pageMargins: [40, 60, 40, 60],
      styles: {
      header: {
        fontSize: 14,
        bold: true,
      },
      },
      };
      
      // Create a new pdfmake instance
      const pdfDoc = pdfMake.createPdf(docDefinition);
      
      // Save and download the PDF
      pdfDoc.download('document.pdf');
      }
      
      async function load_folders() {
      const response = await fetch('/list_folders');
      const folders = await response.json();
      const folderSelect = document.getElementById('folder-select');
      
      folders.forEach((folder) => {
      const option = document.createElement('option');
      option.value = folder;
      option.textContent = folder;
      folderSelect.appendChild(option);
      });
      }
      
      load_folders();
      
      function getFiles() {
      var folder = $('#folder-select').val();
      $.getJSON('/get_files/' + folder, function(data) {
        console.log(data); // Log the data received
        if (data.error) {
            console.error(data.error);
            return;
        }
        var files = data.files;
        $('#file-list').empty();
        for (var i = 0; i < files.length; i++) {
            $('#file-list').append('<li>' + files[i] + '</li>');
        }
      });
      }
      function updateFileList() {
        $.getJSON('/get_updated_files', function(data) {
            var files = data;
            var file_list_element = $('.list-container ul');
            file_list_element.empty();
            for (var i = 0; i < files.length; i++) {
                file_list_element.append('<li><a href="#" onclick="showPDF(\'' + files[i].PresignedURL + '\')">' + files[i].Key + '</a></li>');
            }
        });
      }  
       
       function updateFolderContent() {
        let selectedFolder = $('#folder-selector').val();
        $.post('/get_folder_content', {selected_folder: selectedFolder}, function(data) {
            $('#folder-content').html('');
            for (let item of data.folder_content) {
                let file_url = '/Data/' + selectedFolder + '/' + item;
                // Modify this line to call openPdf function with the Presigned URL
                $('#folder-content').append('<li><a href="#" onclick="openPdf(\'' + file_url + '\')">' + item + '</a></li>');
            }
        });
      }
      
       $('#folder-selector').on('change', updateFolderContent);
      updateFolderContent();
      function setCanvasOpacity() {
      let opacity = 0; // Start with an opacity of 0
      const increaseTime = 5000; // 8 seconds in milliseconds
      const targetOpacity = 0.45; // Change this to your desired opacity
      
      const increaseOpacity = () => {
        opacity += 0.01;
        canvas.style.opacity = opacity;
      
        if (opacity < targetOpacity) {
            setTimeout(increaseOpacity, increaseTime / 100);
        }
      };
      
      setTimeout(increaseOpacity, 0); // Set a delay before starting to increase the opacity
      }
      
      setCanvasOpacity();
       
      const quillContainer = document.querySelector('.quill-container');
      
      
      function wait() {
      var loader = document.getElementById("loader");
      loader.style.display = "block"; 
      }
      function wait2() {
      var loader = document.getElementById("loader2");
      loader.style.display = "block";
      setTimeout(function() {
      loader2.style.display = "none";
      }, 8000); // 8000 milliseconds = 8 seconds
      }
      document.addEventListener("DOMContentLoaded", function () {
      const slider = document.getElementById("opacity-slider");
      const containers = document.querySelectorAll(".down-down-down-side, .right-down-down-side, .left-down-down-side, .quill-container, h4");
      
      slider.addEventListener("input", function () {
      const opacityValue = slider.value / 100;
      
      containers.forEach((container) => {
      container.style.opacity = opacityValue;
      });
      });
      });
       
async function dark(event) {
    event.preventDefault();
       
        const response =  fetch("/dark", {
            method: "POST",
           
        });
      } 

async function light(event) {
                  //  wait();
         event.preventDefault();
      
        const response =  fetch("/light", {
            method: "POST",
           
        });
      } 
       
       quillContainer.addEventListener('input', function() {
  if (quillContainer.textContent.length > 0) {
    quillContainer.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
  } else {
    quillContainer.style.backgroundColor = 'rgba(255, 255, 255, 0)';
  }
});  
     
     
   const toggleCheckbox = document.getElementById('toggleCheckbox');
    const root = document.querySelector(':root');

    toggleCheckbox.addEventListener('change', () => {
      if (toggleCheckbox.checked) {
        root.classList.add('light');
      } else {
        root.classList.remove('light');
      }
    });
       
    const folderSelector = document.getElementById('folder-selector');

    // Load saved values from local storage
    const savedCheckboxState = localStorage.getItem('toggleCheckbox');
    const savedSelectedFolder = localStorage.getItem('folder-selector');

    if (savedCheckboxState) {
      toggleCheckbox.checked = JSON.parse(savedCheckboxState);
         if (toggleCheckbox.checked) {
        root.classList.add('light');
      } else {
        root.classList.remove('light'); 
      }
    }
    if (savedSelectedFolder) {
      folderSelector.value = savedSelectedFolder;
    }

    // Save values to local storage when changed
    toggleCheckbox.addEventListener('change', () => {
      localStorage.setItem('toggleCheckbox', JSON.stringify(toggleCheckbox.checked));
    });

    folderSelector.addEventListener('change', () => {
      localStorage.setItem('folder-selector', folderSelector.value);
    });