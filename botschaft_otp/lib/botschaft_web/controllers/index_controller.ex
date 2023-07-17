defmodule BotschaftWeb.IndexController do
  use BotschaftWeb, :controller

  def index(conn, _params) do
    metrics = Botschaft.Telemetry.get_metrics()
    render(conn, :index, layout: false, metrics: metrics)
  end
end
