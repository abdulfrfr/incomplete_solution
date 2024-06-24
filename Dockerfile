FROM ruby:3.0.2

# Install utilities
RUN apt-get update
RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get -y install \
    nano \
    nodejs && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g yarn

WORKDIR /rails-app

COPY Gemfile Gemfile.lock ./

RUN bundle install

COPY package.json yarn.lock ./

RUN yarn install

COPY . .

# Set environment variables
ENV RAILS_ENV=${RAILS_ENV}
ENV SECRET_KEY_BASE=${SECRET_KEY_BASE}
ENV POSTGRES_HOST=${POSTGRES_HOST}
ENV POSTGRES_NAME=${POSTGRES_NAME}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV SECRET_KEY_BASE=${SECRET_KEY_BASE}
ENV RAILS_MASTER_KEY=${RAILS_MASTER_KEY}
ENV RAILS_SERVE_STATIC_FILES true
ENV RAILS_LOG_TO_STDOUT true

ENTRYPOINT ["./entry.sh"]

# Expose port
EXPOSE 3000
