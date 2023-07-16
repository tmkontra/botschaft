defmodule BotschaftWeb.IndexController do
  use BotschaftWeb, :controller

  def index(conn, _params) do
    render(conn, :index, layout: false)
  end
end
