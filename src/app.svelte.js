import { writable } from 'svelte/store';
import { goto } from '$app/navigation';

export const direction = $state({
  dir: 0
});
export const pages = ['', 'daily', 'weekly'];
let startX = 0;
let endX = 0;

export const currentPage = writable(0);
export const handleTouchStart = (e) => {
  startX = e.touches[0].clientX;
};

export const handleTouchEnd = (e) => {
  endX = e.changedTouches[0].clientX;
  if (startX - endX > 50) {
    navigateToNextPage();
  }
  else if (endX - startX > 50) {
    navigateToPrevPage();
  }
};
export const navigateToPrevPage = () => {
  currentPage.update((page) => {
    console.log(page-1); // print curr page
    if (page > 0) {
      goto('/' + pages[page - 1]);
      return page - 1;
    }
    return page;
  })
  
}
export const navigateToNextPage = () => { 
  currentPage.update((page) => {
    console.log(page+1); // print curr page
    if (page < pages.length - 1) {
      goto('/' + pages[page + 1]);
      return page + 1;
    }
    return page;
  })
}; 

// Function to log the mouse position
let lastX = null;
let timer = null;

export const getMouseDelta = (e) => {
  const currX = e.clientX;
  if(timer) {
    clearTimeout(timer);
  }
  timer = setTimeout(() => {
    if(lastX !== null) {
      const diff = currX - lastX;
      console.log(`Mouse Position: X=${e.clientX}, Y=${e.clientY}`);
      console.log(`Difference in X position after 0.2s: ${diff}`);
      if(diff > 50) {
        console.log("yuh");
        navigateToPrevPage();
      } else if( diff < -50) {
        console.log("boi");
        navigateToNextPage();
      }
    }
    lastX = currX;
  }, 200);
};

// Attach the mousemove event listener
if (typeof window !== 'undefined') {
  window.addEventListener('mousemove', getMouseDelta);
}
