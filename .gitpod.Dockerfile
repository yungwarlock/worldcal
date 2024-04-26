FROM gitpod/workspace-python-3.11:2024-04-26-12-27-08

USER root

RUN curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.gpg | sudo apt-key add - \
     && curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.list | sudo tee /etc/apt/sources.list.d/tailscale.list \
     && apt-get update \
     && apt-get install -y tailscale
RUN update-alternatives --set ip6tables /usr/sbin/ip6tables-nft

RUN echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf \
     && echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf \
     && sudo sysctl -p /etc/sysctl.d/99-tailscale.conf

RUN wget https://github.com/superfly/flyctl/releases/download/v0.2.33/flyctl_0.2.33_Linux_x86_64.tar.gz \
    && tar -xvf flyctl_0.2.33_Linux_x86_64.tar.gz \
    && mv flyctl /usr/local/bin/flyctl \
    && rm flyctl_0.2.33_Linux_x86_64.tar.gz \
    && ln -s /usr/local/bin/flyctl /usr/local/bin/fly
