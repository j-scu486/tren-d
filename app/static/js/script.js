const navSidebarBtn = document.querySelector('#toggle');
const navSideBar = document.querySelector('#navbar')
const modalOverlay = document.querySelector('.modal-overlay');

// Toggle sidenavbar and set modal overlay

navSidebarBtn.addEventListener("click", function(){
  navSideBar.style.transform = "translateX(0)"
  modalOverlay.style.display = "block"
})

window.addEventListener("click", function(e){
  if(e.target == modalOverlay){
    navSideBar.style.transform = "translateX(-100%)";
    modalOverlay.style.display = "none"
  }
})