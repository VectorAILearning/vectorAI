.PHONY: help dev ai-dev prod clean test logs stop logs-dev status restart

help:
	@echo "🚀 VectorAI Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev     - Start full development environment"
	@echo "  make ai-dev  - Start AI development environment with hot reload"
	@echo ""
	@echo "Production:"
	@echo "  make prod    - Start production environment with Nginx"
	@echo ""
	@echo "Control:"
	@echo "  make stop    - Stop all running services"
	@echo "  make restart - Restart all services"
	@echo "  make status  - Show status of all services"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean   - Stop and remove all containers"
	@echo "  make logs    - Show logs from all services"
	@echo "  make logs-dev - Show logs from development services"
	@echo "  make test    - Run tests (placeholder)"
	@echo ""

dev:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose-dev.yml up --build

ai-dev:
	@echo "🤖 Starting AI development environment..."
	@echo "Features: Hot reload, fast iteration, AI-optimized setup"
	docker-compose -f docker-compose-dev.yml up --build -d postgres_ailearning
	@echo "⏳ Waiting for database to be ready..."
	@sleep 5
	docker-compose -f docker-compose-dev.yml up --build api nginx

prod:
	@echo "🚀 Starting production environment..."
	@echo "Building and starting all services for production..."
	docker-compose up --build -d
	@echo "✅ Production environment started!"
	@echo "🌐 Frontend: http://localhost"
	@echo "🔧 API: http://localhost/api/docs"

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker-compose -f docker-compose-dev.yml down -v
	docker system prune -f

logs:
	@echo "📝 Showing production logs..."
	docker-compose logs -f

logs-dev:
	@echo "📝 Showing development logs..."
	docker-compose -f docker-compose-dev.yml logs -f

stop:
	@echo "⏹️ Stopping all services..."
	docker-compose down
	docker-compose -f docker-compose-dev.yml down
	@echo "✅ All services stopped!"

status:
	@echo "📊 Service Status:"
	@echo ""
	@echo "Production services:"
	@docker-compose ps
	@echo ""
	@echo "Development services:"
	@docker-compose -f docker-compose-dev.yml ps

restart:
	@echo "🔄 Restarting services..."
	@make stop
	@make prod

test:
	@echo "🧪 Running tests..."
	@echo "Tests not implemented yet" 