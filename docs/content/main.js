document.addEventListener("DOMContentLoaded", () => {
  const footer = document.querySelector(".wy-nav-content footer");
  if (!footer) return;

  console.log("Adding copyright notice to footer...");

  const copyright = document.createElement("div");
  copyright.style.textAlign = "left";
  copyright.style.paddingTop = "1rem";
  copyright.style.fontSize = "16px";
  copyright.style.color = "#888";
  copyright.style.marginTop = "0.75rem";

  const year = new Date().getFullYear();
copyright.innerHTML = `Copyright © 2025 - ${year} ⦿ <a href="https://abhigupta.io" style="text-decoration: none;">Abhinav Gupta</a>`;

  footer.appendChild(copyright);
});
