# syntax=docker/dockerfile:1
 FROM archlinux:latest
 WORKDIR /hat
 COPY . .
 RUN cp docker/mirrorlist /etc/pacman.d/mirrorlist
 RUN pacman -Sy
 RUN pacman -Sy $(< requirements.archlinux.txt) --noconfirm
 RUN pip install -r requirements.pip.txt
