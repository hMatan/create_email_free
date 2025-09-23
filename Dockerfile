FROM jenkins/jenkins:lts

USER root

# התקנות בסיסיות
RUN apt-get update && apt-get install -y \
    curl wget gnupg lsb-release ca-certificates \
    python3 python3-pip xvfb unzip \
    && rm -rf /var/lib/apt/lists/*

# התקנת Chrome (נשאיר למקרה שנצליח לתקן)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# התקנת Firefox ESR (יציב יותר בDocker)
RUN apt-get update && apt-get install -y \
    firefox-esr \
    && rm -rf /var/lib/apt/lists/*

# התקנת GeckoDriver לFirefox
RUN GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep tag_name | cut -d '"' -f 4) \
    && wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" \
    && tar -xzf /tmp/geckodriver.tar.gz -C /tmp/ \
    && mv /tmp/geckodriver /usr/bin/geckodriver \
    && chmod +x /usr/bin/geckodriver \
    && rm /tmp/geckodriver.tar.gz

# הגדרת משתנה סביבה לעקיפת ההגבלה
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# התקנת Python packages
RUN pip3 install --no-cache-dir \
    selenium>=4.10.0 \
    requests \
    beautifulsoup4

# הגדרות סביבה
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV FIREFOX_BIN=/usr/bin/firefox-esr

# הגדרת Xvfb
RUN echo '#!/bin/bash\nexport DISPLAY=:99\nXvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\nexec "$@"' > /usr/local/bin/start-xvfb.sh \
    && chmod +x /usr/local/bin/start-xvfb.sh

USER jenkins

ENTRYPOINT ["/usr/local/bin/start-xvfb.sh", "/usr/local/bin/jenkins.sh"]
