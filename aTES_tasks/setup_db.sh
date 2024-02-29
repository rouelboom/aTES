#!/bin/sh

DB_NAME=aTES_tasks

# Create database
psql -d postgres -U postgres -c "create database ${DB_NAME};"
