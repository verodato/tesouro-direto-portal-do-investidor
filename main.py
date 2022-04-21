from portal_tesouro import PortalTesouro


def main():
    driver = PortalTesouro()
    driver.start_scraping()


if __name__ == '__main__':
    main()
