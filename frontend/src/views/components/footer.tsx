import React from "react";

interface Props {}
function Footer(props: Props) {
  return (
    <footer className="page-footer">
      <div className="container">
        <p className="copyrights">
          Designed & Developed by <a href="https://www.linkedin.com/in/ahmedhrayyan/">Ahmed Hamed</a>
        </p>
      </div>
    </footer>
  )
}

export default Footer;
