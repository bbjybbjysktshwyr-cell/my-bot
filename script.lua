-- Steal An Egg - Universal Return To Bas Hub 🛡️
local Players = game:GetService("Players")
local CoreGui = game:GetService("CoreGui")
local LocalPlayer = Players.LocalPlayer

if CoreGui:FindFirstChild("EggHubGui") then
    CoreGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
pcall(function() ScreenGui.Parent = CoreGui end)
if not ScreenGui.Parent then ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui") end
ScreenGui.ResetOnSpawn = false

-- النافذة الرئيسية
local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.3, 0, 0.3, 0)
MainFrame.Size = UDim2.new(0, 260, 0, 160)
MainFrame.Active = true
MainFrame.Draggable = true

-- العنوان
local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Return To Base Hub 🛡️"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- زر العودة للبداية / القاعدة
local SpawnBtn = Instance.new("TextButton")
SpawnBtn.Parent = MainFrame
SpawnBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SpawnBtn.Position = UDim2.new(0.1, 0, 0.45, 0)
SpawnBtn.Size = UDim2.new(0.8, 0, 0, 50)
SpawnBtn.Text = "العودة للبداية / القاعدة 🛡️"
SpawnBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SpawnBtn.TextSize = 15
SpawnBtn.Font = Enum.Font.SourceSansBold

-- دالة العودة القسرية لمركز البداية الأول للماب
SpawnBtn.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local root = char.HumanoidRootPart
        
        -- إحداثيات مركز البداية الأساسية في بداية الماب (أول قاعدة)
        local baseOrigin = CFrame.new(0, 10, 0)
        
        -- البحث عن أول قاعدة أو مكان رسبون أساسي
        for _, obj in ipairs(workspace:GetDescendants()) do
            if obj:IsA("SpawnLocation") and (obj.Position.Magnitude < 150) then
                baseOrigin = obj.CFrame + Vector3.new(0, 4, 0)
                break
            end
        end
        
        -- تفريغ الفيزياء ونقل الشخصية مباشرة متجاوزين حماية المراحل المتقدمة
        root.AssemblyLinearVelocity = Vector3.zero
        root.AssemblyAngularVelocity = Vector3.zero
        
        char:PivotTo(baseOrigin)
        
        task.wait(0.05)
        root.AssemblyLinearVelocity = Vector3.zero
    end
end)
