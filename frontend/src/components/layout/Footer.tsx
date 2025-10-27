import React from 'react';
import { Layout } from 'antd';

const { Footer: AntFooter } = Layout;

const Footer: React.FC = () => {
  return (
    <AntFooter style={{ textAlign: 'center', background: '#f0f2f5' }}>
      © 2025 HWP Report Generator | Powered by KJBank R&D HanTJ
    </AntFooter>
  );
};

export default Footer;
