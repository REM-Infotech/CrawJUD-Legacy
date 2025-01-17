FROM python:3

# Atualizar pacotes e configurar locales
RUN apt-get update && apt-get install -y locales && \
    sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    apt-get clean

ENV TERM xterm
ENV LANG=pt_BR.UTF-8
ENV LC_ALL=pt_BR.UTF-8

# Instalar Chrome e TightVNCServer e suas dependências
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    tightvncserver \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    fonts-liberation \
    --no-install-recommends && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Configurar o TightVNCServer no display :99 com resolução 1600x900 e proporção 16:9
RUN mkdir -p ~/.vnc && echo "password" | vncpasswd -f > ~/.vnc/passwd && \
    chmod 600 ~/.vnc/passwd && \
    echo "#!/bin/bash\nexec /usr/bin/tightvncserver :99 -geometry 1600x900 -depth 24" > ~/.vnc/xstartup && \
    chmod +x ~/.vnc/xstartup && \
    tightvncserver :99 -geometry 1600x900 -depth 24

# Instalar Poetry
RUN pip install --no-cache-dir poetry

# Criar diretório de trabalho e copiar arquivos
WORKDIR /crawjud_backend
ADD . /crawjud_backend

# Instalar dependências
RUN poetry config virtualenvs.in-project true && poetry install --no-root

EXPOSE 8000

# Comando padrão
CMD ["poetry", "run", "python", "-m", "app"]
