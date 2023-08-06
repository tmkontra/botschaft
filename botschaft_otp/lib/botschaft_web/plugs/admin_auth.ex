defmodule BotschaftWeb.Plugs.AdminAuth do
  import Plug.Conn

  def init(_) do
  end

  def call(%Plug.Conn{params: %{"locale" => loc}} = conn, _default) do
    assign(conn, :locale, loc)
  end

  def call(conn, default) do
    assign(conn, :locale, default)
  end
end
