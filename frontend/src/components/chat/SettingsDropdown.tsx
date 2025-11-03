import React, { forwardRef } from "react";
import { GlobalOutlined } from "@ant-design/icons";
import styles from "./SettingsDropdown.module.css";

interface SettingsDropdownProps {
  webSearchEnabled: boolean;
  onWebSearchChange: (enabled: boolean) => void;
}

const SettingsDropdown = forwardRef<HTMLDivElement, SettingsDropdownProps>(
  ({ webSearchEnabled, onWebSearchChange }, ref) => {
    return (
      <div ref={ref} className={styles.dropdown}>
        <button
          className={`${styles.dropdownItem} ${
            webSearchEnabled ? styles.active : ""
          }`}
          onClick={() => onWebSearchChange(!webSearchEnabled)}
        >
          <div className={styles.dropdownLabel}>
            <GlobalOutlined />
            <span>웹 검색</span>
          </div>
        </button>
      </div>
    );
  }
);

SettingsDropdown.displayName = "SettingsDropdown";

export default SettingsDropdown;
