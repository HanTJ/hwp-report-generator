import React from 'react'
import {Layout} from 'antd'
import styles from './Footer.module.css'

const {Footer: AntFooter} = Layout

interface FooterProps {
    sidebarCollapsed?: boolean | null
}

const Footer = ({sidebarCollapsed = null}: FooterProps) => {
    const getFooterClass = () => {
        if (sidebarCollapsed === null) {
            return styles.noSidebar
        }
        return sidebarCollapsed ? styles.sidebarCollapsed : styles.sidebarExpanded
    }

    return <AntFooter className={`${styles.footer} ${getFooterClass()}`}>© 2025 HWP Report Generator | Powered by R&D</AntFooter>
}

export default Footer
