#!/bin/sh

DB_NAME=ates_tasks

# Create database
psql -d postgres -U postgres -c "create database ${DB_NAME};"
