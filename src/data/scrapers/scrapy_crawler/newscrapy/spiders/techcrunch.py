import scrapy


class TechcrunchSpider(scrapy.Spider):
    name = "techcrunch"
    allowed_domains = ["techcrunch.com"]
    start_urls = ["https://techcrunch.com/latest/"]

    def parse(self, response):
        # Extract articles from the WordPress block structure
        articles = response.css('li.wp-block-post')
        for article in articles:
            # Get the href link to the article page
            article_link = article.css('h3.loop-card__title a.loop-card__title-link::attr(href)').extract_first()
            # Get basic article information from the listing page
            title = article.css('h3.loop-card__title a.loop-card__title-link::text').extract_first()
            # Create the full URL for the article page and follow it
            if article_link:
                yield response.follow(
                    article_link,
                    callback=self.parse_article_detail,
                    meta={
                        'title': title,
                        'article_url': article_link
                    }
                )
        self.check_for_next_page(response)

    def parse_article_detail(self, response):
        # Get the data passed from the main page
        title = response.meta['title']
        article_url = response.meta['article_url']

        # Extract article content from the individual article page
        try:
            author = response.css('.wp-block-tc23-author-card-name__link::text').extract_first()
            # Publication date - extract both datetime and readable format
            date_datetime = response.css('.wp-block-post-date time::attr(datetime)').extract_first()
            date_readable = response.css('.wp-block-post-date time::text').extract_first()
            summary = response.css('p#speakable-summary::text').extract_first()
            tags = response.css('.tc23-post-relevant-terms__terms a::text').extract()
        except Exception as e:
            self.logger.error(f"Error extracting article details from {article_url}: {e}")
            # Set default values if extraction fails
            author = None
            date_datetime = None
            date_readable = None
            tags = []
            summary = None
        yield {
            'title': title,
            'url': article_url,
            'author': author,
            'publication_date_datetime': date_datetime,
            'publication_date_readable': date_readable,
            'summary': summary,
            'tags': tags
        }

    def check_for_next_page(self, response):
        # Look for next page button
        next_page_url = response.css('a.wp-block-query-pagination-next::attr(href)').extract_first()
        if next_page_url:
            self.logger.info(f"Found next page: {next_page_url}")
            try:
                user_input = input(
                    f"\nFinished scraping current page. Next page available: {next_page_url}\nEnter '1' to continue to next page, or any other key to stop: ").strip()
                if user_input == '1':
                    self.logger.info("User chose to continue to next page")
                    # Follow the next page URL
                    yield response.follow(
                        next_page_url,
                        callback=self.parse,
                        dont_filter=True  # Allow revisiting pages
                    )
                else:
                    self.logger.info("User chose to stop scraping")

            except KeyboardInterrupt:
                self.logger.info("Scraping interrupted by user")
                return
        else:
            self.logger.info("No next page found - scraping complete")