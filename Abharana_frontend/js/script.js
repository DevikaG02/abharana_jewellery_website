function toggleMenu(){document.getElementById("mobileMenu")?.classList.toggle("open")}
function openSearch(){const el=document.getElementById("searchOverlay");if(!el)return;el.classList.add("open");el.setAttribute("aria-hidden","false");setTimeout(()=>document.getElementById("searchInput")?.focus(),100)}
function closeSearch(){const el=document.getElementById("searchOverlay");if(!el)return;el.classList.remove("open");el.setAttribute("aria-hidden","true")}
function subscribe(event){event.preventDefault();alert("Thank you for your interest in the Aurelia Journal. Newsletter signup needs a backend connection to save your email.");event.target.reset()}
document.addEventListener("keydown",event=>{if(event.key==="Escape"){closeSearch();document.getElementById("mobileMenu")?.classList.remove("open")}})
