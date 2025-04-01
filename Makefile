dc-up:
	docker compose -f docker-compose.local.yml up
dc-down:
	docker compose -f docker-compose.local.yml down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.DS_Store" -delete
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	@echo "Cleaned up temporary files."

project_tree:
	tree -a -I ".venv|.git|.vscode|.idea|node_modules|migrations|admin|.mypy_cache|__pycache__|htmlcov|frontend|postman_collection|docs|media"
