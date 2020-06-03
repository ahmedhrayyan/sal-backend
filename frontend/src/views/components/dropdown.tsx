import React, {
  FunctionComponent,
  ReactNode,
  Children,
  cloneElement,
  useState,
  useRef,
} from "react";

interface Props {
  btnContent: ReactNode;
  btnClass?: string;
}

const Dropdown: FunctionComponent<Props> = ({
  btnContent,
  btnClass,
  children,
}) => {
  const [active, setActive] = useState<boolean>(false);

  function toggleMenu(evt: React.MouseEvent<HTMLButtonElement>) {
    if (active === true) {
      setActive(false)
    } else {
      setActive(true)
    }
  }

  return (
    <div className="dropdown">
      <button
        className={btnClass ? btnClass + " btn" : "btn"}
        aria-haspopup="true"
        aria-expanded={active}
        onClick={toggleMenu}
      >
        {btnContent}
      </button>

      <div
        className={active ? "dropdown-menu show" : "dropdown-menu"}
        aria-labelledby="dropdownMenuLink"
      >
        {Children.map(children, (child: any) => {
          return cloneElement(child, {
            className: child.props.className
              ? child.props.className + " dropdown-item"
              : "dropdown-item",
          });
        })}
      </div>
    </div>
  );
};

export default Dropdown;
