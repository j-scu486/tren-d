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

// Product Select

const thumbImage = document.querySelectorAll('.thumb')
const imageContainer = document.querySelector('.product-image');

let thumbImageArray = [];
let counter = 0;

thumbImage.forEach((image) => {
  thumbImageArray.push(image.src)
})

// Change image on arrow (Like a carousel)
const btnNext = document.querySelector('.btn-next');
const btnPrev = document.querySelector('.btn-prev');

btnNext.addEventListener("click", function(){
  if(counter < 2){
    counter++;
  } else {
    counter = 0;
  }

  imageContainer.innerHTML = `
  <img src="${thumbImageArray[counter]}"></img>
  `
})

btnPrev.addEventListener("click", function(){
  if(counter > 0){
    counter--;
  } else {
    counter = 2;
  }
  console.log(counter)
  imageContainer.innerHTML = `
  <img src="${thumbImageArray[counter]}"></img>
  `
})

// Change thumbimage on click
thumbImage.forEach((image) => {
  image.addEventListener("click", function(e){
    imageSource = e.target.src;
    imageContainer.innerHTML = `<img src="${imageSource}"></img>`
  })
})
