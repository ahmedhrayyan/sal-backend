import React, { FunctionComponent } from "react";

interface Props {
  src: string;
  size?: string;
  info?: {
    name: string;
    role?: string;
  };
}

const Avatar: FunctionComponent<Props> = ({ src, size, info }) => {
  return (
    <div className={`avatar-${size}`}>
      <div className="avatar-img">
        <img src={src} alt={info ? info.name + " image" : "avatar image"} />
      </div>
      {info && (
        <p className="avatar-info">
          {info.name}
          {info.role && (
            <>
              <br />
              <span className="role">{info.role}</span>
            </>
          )}
        </p>
      )}
    </div>
  );
};
Avatar.defaultProps = {
  size: "md",
};

export default Avatar;
