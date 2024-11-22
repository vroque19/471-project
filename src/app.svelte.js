import { writable } from 'svelte/store';
import { goto } from '$app/navigation';

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
    console.log(page);
    if (page > 0) {
      goto('/' + pages[page - 1]);
      return page - 1;
    }
    return page;
  })
  
}
export const navigateToNextPage = () => {
  currentPage.update((page) => {
    console.log(page);
    if (page < pages.length - 1) {
      goto('/' + pages[page + 1]);
      return page + 1;
    }
    return page;
  })
}; 


