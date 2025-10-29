import React from 'react';
import { Layout } from 'antd';
import styles from './Footer.module.css';

const { Footer: AntFooter } = Layout;

const Footer: React.FC = () => {
  return (
    <AntFooter className={styles.footer}>
      © 2025 HWP Report Generator | Powered by KJBank R&D HanTJ
    </AntFooter>
  );
};

export default Footer;
