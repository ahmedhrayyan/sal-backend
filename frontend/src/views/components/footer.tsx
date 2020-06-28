import React from "react";

interface Props {}
function Footer(props: Props) {
  return (
    <footer className="page-footer">
      <div className="container">
        <p className="copyrights">
          Designed & Developed by&nbsp;
          <a
            href="https://www.linkedin.com/in/ahmedhrayyan/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Ahmed Hamed
          </a>
        </p>
      </div>
    </footer>
  );
}

export default Footer;
