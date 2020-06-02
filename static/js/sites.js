var isInit = false;
function openModal(){
  var elModal  = document.querySelector('#Modal');
  if(isInit===false) {
   isInit = true;
   document.querySelector('.prefix-close').addEventListener('click',
        function(event) {
           event.preventDefault();
           elModal.classList.toggle('active');
        }
    );
  }
  elModal.classList.toggle('active');
}